/* Copyright 2012-2017 Ministerie van Sociale Zaken en Werkgelegenheid
 *
 * Licensed under the Apache License, Version 2.0 (the "License")
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import React from 'react';

import {DomainObjectsTable, RequirementsTable, MetricClassesTable,
        MetricSourcesTable} from 'components/meta_data_table.js';
import {Loader} from 'widgets/loader.js';


class Help extends React.Component {
    constructor() {
        super();
        this.state = {meta_data: 'loading'};
    }

    componentDidMount() {
        var self = this;
        $.getJSON("json/meta_data.json", "", function(meta_data) {
            self.setState({meta_data: meta_data});
        });
    }

    render () {
        if (this.state.meta_data === 'loading') {
            return <Loader/>;
        } else {
            return (
                <div>
                    <h2 id="help_about">Over HQ</h2>
                    <div className="alert alert-info" role="alert">
                        <strong>HQ versie {this.props.hq_version}</strong>. Zie <a className="alert-link"
                        href="https://github.com/ICTU/quality-report/blob/master/docs/CHANGES.md" target="_blank">
                        wijzigingsgeschiedenis</a>.
                    </div>
                    <p>
                        HQ (Holistic Software Quality Reporting) is een geautomatiseerd systeem dat het mogelijk
                        maakt frequent metingen te doen aan de producten, processen en teams binnen
                        softwareontwikkelprojecten en op basis daarvan kwaliteitsrapportages te genereren.
                        De rapportages geven inzicht in de kwaliteit van de producten en de
                        uitvoering van processen van een project, maken eventuele technische schuld inzichtelijk
                        en geven aan waar actie benodigd is om technische schuld juist te voorkomen.
                    </p>
                    <p>
                        HQ haalt de benodigde meetgegevens uit andere tools en rapportages die toch al vaak gebruikt
                        worden bij softwareontwikkeling, zoals SonarQube, Jenkins, JaCoCo, NCover, Nexus, Git,
                        Subversion, etc.
                    </p>
                    <h3>
                        Voor wie is het kwaliteitssysteem bedoeld?
                    </h3>
                    <p>
                        HQ is primair bedoeld voor projectleiders, ontwerpers,
                        ontwikkelaars en testers van softwareontwikkelprojecten. Projectleiders kunnen zien in
                        hoeverre de kwaliteit van hun project(en) voldoet aan de kwaliteitscriteria. Ontwerpers,
                        ontwikkelaars en testers kunnen zien in hoeverre hun werk voldoet aan de kwaliteitscriteria
                        en waar eventueel nog verbeteringen moeten worden doorgevoerd.
                    </p>
                    <p>
                        Daarnaast laten de kwaliteitsrapportages aan direct betrokkenen zoals opdrachtgever,
                        beheerders en andere belanghebbenden zien dat de kwaliteit van de producten die
                        binnen een project worden gebouwd voldoen aan de kwaliteitscriteria.
                    </p>
                    <h3>
                        Waar zijn de normen op gebaseerd?
                    </h3>
                    <p>
                        De metingen en de normen voor de metingen zijn deels gebaseerd op de <a
                        href="http://www.sig.eu/en/Services/Software%%20Product%%20Certification/Evaluation%%20Criteria/" target="_blank">
                        SIG-TUViT Evaluation Criteria for Trusted Product Maintainability</a>. Daarnaast zijn de
                        metingen en de normen gebaseerd op het Scrumproces.
                        Welke metingen in een rapportage zijn opgenomen hangt af van de eisen die voor het project
                        gelden, zie hieronder.
                    </p>
                    <h3>
                        Wat meet HQ?
                    </h3>
                    <p>
                        HQ meet (kwaliteits)eigenschappen van de softwareproducten, het proces en de teams.
                    </p>
                    <dl className="dl-horizontal">
                        <dt>
                            Software
                        </dt>
                        <dd>
                            Om de lange-termijn onderhoudbaarheid van de software te bevorderen meet HQ
                            (met behulp van SonarQube; een tool voor metingen aan software) kenmerken
                            van de software zoals complexiteit, lengte en overtredingen van <em>good practices</em>.
                        </dd>
                        <dt>
                            Proces
                        </dt>
                        <dd>
                            Om te zorgen dat het proces goed wordt uitgevoerd meet HQ of
                            werkproducten zoals user stories en logische testgevallen zijn gereviewd en goedgekeurd.
                        </dd>
                        <dt>
                            Teams
                        </dt>
                        <dd>
                            HQ meet de velocity van de teams en de stemming binnen de teams.
                        </dd>
                    </dl>

                    <h2 id="help_on_domain_objects">Domeinobjecten</h2>
                    <p>
                        Hieronder de lijst van domeinobjecten waaraan HQ kan meten. Per
                        domeinobject is aangegeven of het domeinobject voorkomt in deze rapportage.
                        Bij ieder domeinobject staan de eisen die
                        standaard van toepassing zijn op het domeinobject.
                    </p>
                    <DomainObjectsTable domain_objects={this.state.meta_data['domain_objects']} />

                    <h2 id="help_on_requirements">Eisen</h2>
                    <p>
                        Hieronder de lijst van eisen die HQ kan borgen. Per
                        eis is aangegeven of de eis van toepassing is op het project. Of een eis van toepassing is,
                        is in de project definitie geconfigureerd. Bij iedere eis staan de metrieken die gemeten
                        worden als de betreffende eis van toepassing is (zie <a href="#help_on_metrics">Metrieken</a>).
                    </p>
                    <RequirementsTable requirements={this.state.meta_data['requirements']} />

                    <h2 id="help_on_metrics">Metrieken</h2>
                    <p>
                        Hieronder de lijst van metrieken die HQ kan meten. Per metriek is
                        aangegeven of de metriek in dit rapport gemeten wordt. Of een metriek gemeten wordt
                        hangt af van de eisen die van toepassing zijn op het project
                        (zie <a href="#help_on_requirements">Eisen</a>).
                    </p>
                    <MetricClassesTable metric_classes={this.state.meta_data['metrics']} />

                    <h2 id="help_on_metric_sources">Metriekbronnen</h2>
                    <p>
                        Hieronder de lijst van metriekbronnen die HQ kan raadplegen. Per
                        metriekbron is aangegeven of de metriekbron in dit rapport gebruikt wordt. Of een
                        metriekbron gebruikt wordt hangt af van de metrieken die van gemeten worden
                        (zie <a href="#help_on_metrics">Metrieken</a>).
                    </p>
                    <MetricSourcesTable metric_sources={this.state.meta_data['metric_sources']} />

                    <h2 id="help_on_configuration">Configuratie</h2>
                    <p>
                        De configuratie van HQ vindt grotendeels
                        plaats met behulp van een project definitie die beschreven
                        wordt in een <code>project_definition.py</code> python bestand.
                        Zie <a href="https://github.com/ICTU/quality-report" target="_blank">Github</a> voor
                        meer informatie en voorbeelden.
                    </p>
                </div>
            )
        }
    }
}

export {Help};
